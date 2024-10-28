using Live2D.Cubism.Core;
using UnityEngine;

namespace Live2D.Cubism.Framework.MouthMovement
{
    /// <summary>
    /// Controls <see cref="CubismMouthParameter"/>s.
    /// </summary>
    public sealed class CubismMouthController : MonoBehaviour, ICubismUpdatable
    {
        [SerializeField]
        public CubismParameterBlendMode BlendMode = CubismParameterBlendMode.Override;

        [SerializeField, Range(0f, 1f)]
        public float MouthOpening = 1f;

        private CubismParameter[] Destinations { get; set; }

        [HideInInspector]
        public bool HasUpdateController { get; set; }

        public void Refresh()
        {
            var model = this.FindCubismModel();

            if (model == null)
            {
                return;
            }

            var tags = model
                .Parameters
                .GetComponentsMany<CubismMouthParameter>();

            Destinations = new CubismParameter[tags.Length];

            for (var i = 0; i < tags.Length; ++i)
            {
                Destinations[i] = tags[i].GetComponent<CubismParameter>();
            }

            HasUpdateController = (GetComponent<CubismUpdateController>() != null);
        }

        public int ExecutionOrder
        {
            get { return CubismUpdateExecutionOrder.CubismMouthController; }
        }

        public bool NeedsUpdateOnEditing
        {
            get { return false; }
        }

        public void OnLateUpdate()
        {
            if (!enabled || Destinations == null)
            {
                return;
            }

            Destinations.BlendToValue(BlendMode, MouthOpening);
        }

        public void SetMouthOpening(float value)
        {
            MouthOpening = Mathf.Clamp(value, 0f, 1f);
        }

        private void Start()
        {
            Refresh();
        }

        private void LateUpdate()
        {
            if (!HasUpdateController)
            {
                OnLateUpdate();
            }
        }
    }
}